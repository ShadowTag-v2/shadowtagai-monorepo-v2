# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""aiyou-core package — shared infrastructure for the daemon fleet."""


def ping() -> str:
  """Health check sentinel. Returns 'pong'."""
  return "pong"
