"""
Verification Script for Pnkln Ingestion
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pnkln.tools.finance import mcarlo_bundle

from src.pnkln.verticals.odor import odor_sim


class TestPnklnIngest(unittest.TestCase):
    def test_mcarlo_bundle(self):
        """Test Monte Carlo bundle logic (pure computation)."""
        cfg = {"test_comp": {"n": 100, "base": 100.0, "sd": 10.0, "gr": 0.1, "mult": 2.0}}
        res = mcarlo_bundle(cfg)
        self.assertIn("sum_mean", res)
        self.assertIn("components", res)
        self.assertGreater(res["sum_mean"], 0)
        print(f"Monte Carlo Result: {res['sum_mean']}")

    def test_odor_sim(self):
        """Test Odor simulation logic (NumPy)."""
        res = odor_sim(n=32, src=[(16, 16, 1.0)])
        self.assertEqual(res.shape, (32, 32))
        self.assertGreater(res.max(), 0)
        print(f"Odor Max Signal: {res.max()}")

    @patch("src.pnkln.verticals.swiper.GenerativeModel")
    def test_swiper_plan(self, mock_model_cls):
        """Test Swiper Plan (Mocked Gemini)."""
        from src.pnkln.verticals.swiper import swiper_plan

        mock_model = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Mocked Plan"
        mock_model.generate_content.return_value = mock_resp
        mock_model_cls.return_value = mock_model

        res = swiper_plan("Test Query")
        self.assertEqual(res, "Mocked Plan")
        print("Swiper Plan Mock Test Passed")


if __name__ == "__main__":
    unittest.main()
