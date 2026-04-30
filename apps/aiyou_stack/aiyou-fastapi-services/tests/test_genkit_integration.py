"""Verification script for Genkit integration.
Tests initialization and basic flow execution.
"""

from __future__ import annotations

import logging
import sys
import unittest

# Ensure src is in path
sys.path.append("src")

from src.antigravity import genkit_ops
from src.antigravity.genkit_wrapper import get_genkit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGenkitIntegration(unittest.TestCase):
    def test_initialization(self):
        """Test that Genkit initializes correctly."""
        gk = get_genkit()
        self.assertIsNotNone(gk)
        # Verify it returns the same instance
        gk2 = get_genkit()
        self.assertIs(gk, gk2)

    def test_flow_registration(self):
        """Test that the ops flow is registered and callable."""
        # Ensure flows are defined
        genkit_ops.define_ops_flows()

        get_genkit()
        # In a real SDK, we'd inspect the registry.
        # Here we just verify the function exists and runs given our wrapper implementation.
        # We manually test the function logic for now since we can't easily invoke the
        # flow registry without a full server context in this unit test.

        # Test direct function call (logic test)
        result_status = genkit_ops.antigravity_ops_flow("status")
        self.assertIn("System Status", result_status)

        result_deploy = genkit_ops.antigravity_ops_flow("deploy")
        self.assertIn("Deployment Status", result_deploy)


if __name__ == "__main__":
    unittest.main()
