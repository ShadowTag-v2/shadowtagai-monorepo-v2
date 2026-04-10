import datetime
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# Mock external dependencies before importing gemini_core
sys.modules["vertexai"] = MagicMock()
sys.modules["vertexai.generative_models"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.generativeai.types"] = MagicMock()
sys.modules["redis"] = MagicMock()

from shadowtag_v4.services.gemini_core import MODEL_FALLBACK_CHAIN, GeminiAntigravity


class TestGeminiFailover(unittest.TestCase):
    def setUp(self):
        # Mock init to avoid real API calls
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
            self.gemini = GeminiAntigravity(api_key="fake_key")

        # Mock _switch_model and _is_rate_limited
        self.gemini._switch_model = MagicMock()
        self.gemini._is_rate_limited = MagicMock(return_value=False)
        self.gemini._mark_rate_limited = MagicMock()

    @patch("shadowtag_v4.services.gemini_core.datetime")
    def test_failover_blocked_outside_break(self, mock_datetime):
        # Set time to 12:00 PM (Outside 01:00-06:00 break)
        mock_now = datetime.datetime(2025, 12, 8, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        # Mock function that fails
        mock_fn = MagicMock(side_effect=[Exception("429 Rate Limit"), Exception("Success?")])

        # Expect the original error to be raised
        with self.assertRaises(Exception) as cm:
            self.gemini._execute_with_fallback(mock_fn)

        self.assertEqual(str(cm.exception), "429 Rate Limit")
        # Should only have tried the first model (attempt 0)
        self.assertEqual(mock_fn.call_count, 1)

    @patch("shadowtag_v4.services.gemini_core.datetime")
    def test_failover_allowed_inside_break(self, mock_datetime):
        # Set time to 02:00 AM (Inside 01:00-06:00 break)
        mock_now = datetime.datetime(2025, 12, 8, 2, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        # Mock function that fails on first call, succeeds on second
        mock_fn = MagicMock(side_effect=[Exception("429 Rate Limit"), "Success"])

        result = self.gemini._execute_with_fallback(mock_fn)

        self.assertEqual(result, "Success")
        # Should have tried twice (attempt 0 fail, attempt 1 success)
        self.assertEqual(mock_fn.call_count, 2)
        # Should have switched model
        self.gemini._switch_model.assert_called_with(MODEL_FALLBACK_CHAIN[1])


if __name__ == "__main__":
    unittest.main()
