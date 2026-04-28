# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from src.pnkln.gemini_integration import GeminiCostTracker
from src.pnkln.intelligence_api import EnrichmentType, IntelligenceAPI


def test_cost_tracker():
    print("Testing GeminiCostTracker...")
    tracker = GeminiCostTracker()
    # 1M tokens in, 1M tokens out
    # GPT4: $30 + $60 = $90
    # Gemini: $0.50 + $1.50 = $2.00
    # Savings: $88.00
    tracker.track(1_000_000, 1_000_000)
    print(f"Savings calculated: ${tracker.saved_cost:.4f}")
    assert abs(tracker.saved_cost - 88.0) < 0.01, (
        f"Expected ~$88.00 savings, got {tracker.saved_cost}"
    )
    print("PASS")


def test_intelligence_api():
    print("Testing IntelligenceAPI...")
    api = IntelligenceAPI()
    cust_id = "test_customer"

    # 1 sentiment analysis ($0.01)
    api.log_usage(cust_id, EnrichmentType.SENTIMENT)

    bill = api.get_current_bill(cust_id)
    print(f"Bill calculated: ${bill:.4f}")
    assert bill == 0.01, f"Expected $0.01, got {bill}"
    print("PASS")


if __name__ == "__main__":
    try:
        test_cost_tracker()
        test_intelligence_api()
        print("\nAll Revenue Logic Tests PASSED")
    except Exception as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)
