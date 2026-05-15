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

    # Test exact match
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
      cm.detect_break(tools, system, 0)
    self.assertEqual(f.getvalue(), "")

    # Test break
    f = io.StringIO()
    tools["bash"]["type"] = "tool"
    with redirect_stdout(f):
      cm.detect_break(tools, system, 0)
    self.assertIn("CACHE BUST DETECTED: bash changed.", f.getvalue())


if __name__ == "__main__":
  unittest.main()
