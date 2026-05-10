# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for DSPy Swarm Router."""

import unittest
from swarm_config import SwarmConfig, SwarmEndpoint


class TestSwarmConfig(unittest.TestCase):
  def test_default_config(self):
    cfg = SwarmConfig()
    self.assertEqual(cfg.fallback_model, "gemini-3.1-flash-lite-preview")
    self.assertEqual(cfg.timeout_seconds, 30)
    self.assertEqual(len(cfg.endpoints), 0)

  def test_endpoint_lookup(self):
    ep = SwarmEndpoint("local", "127.0.0.1", 8080, "gemma-4", "sidekick")
    cfg = SwarmConfig(endpoints=[ep])
    found = cfg.get_endpoint("sidekick")
    self.assertIsNotNone(found)
    self.assertEqual(found.name, "local")

  def test_missing_role_returns_none(self):
    cfg = SwarmConfig()
    self.assertIsNone(cfg.get_endpoint("nonexistent"))


if __name__ == "__main__":
  unittest.main()
