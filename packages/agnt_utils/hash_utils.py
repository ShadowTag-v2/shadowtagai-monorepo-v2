# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""hash_utils — deterministic hashing for cache keys and change detection.

Ported from Claude Code v2.1.91 ``hash.ts``.
Provides djb2 (non-cryptographic, 32-bit) and SHA-256 hashing.  Uses only
the standard library — zero external dependencies.
"""

from __future__ import annotations

import ctypes
import hashlib


def djb2_hash(text: str) -> int:
  """Compute the djb2 hash of *text*, returning a signed 32-bit integer.

  Deterministic across Python versions.  Use for stable on-disk cache
  directory names and non-cryptographic bucketing.

  This mirrors the original TypeScript implementation which uses
  ``((hash << 5) - hash + charCode) | 0`` for signed 32-bit overflow.
  """
  h = 0
  for ch in text:
    h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
  # Convert unsigned 32-bit to signed 32-bit (match JS ``| 0``).
  return ctypes.c_int32(h).value


def hash_content(content: str) -> str:
  """SHA-256 hex digest of *content* for change detection."""
  return hashlib.sha256(content.encode("utf-8")).hexdigest()


def hash_pair(a: str, b: str) -> str:
  """Hash two strings without concatenating them.

  Uses incremental SHA-256 update with a null separator to distinguish
  ``("ts", "code")`` from ``("tsc", "ode")``.
  """
  h = hashlib.sha256()
  h.update(a.encode("utf-8"))
  h.update(b"\x00")
  h.update(b.encode("utf-8"))
  return h.hexdigest()
