import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.core.prompt_cache import CacheManager


class TestPromptCache(unittest.TestCase):
  def test_cache_bust_detection(self):
    cm = CacheManager()
    tools = {"bash": {"type": "function"}}
    system = "Hello<DYNAMIC_BOUNDARY>World"
    cm.detect_break(tools, system, 100)

    # Test exact match — no changes expected
    changes = cm.detect_break(tools, system, 0)
    self.assertEqual(changes, [])

    # Test break — mutate a tool, expect it in changes list
    tools["bash"]["type"] = "tool"
    changes = cm.detect_break(tools, system, 0)
    self.assertIn("bash", changes)


if __name__ == "__main__":
  unittest.main()
