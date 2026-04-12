# /antigravity/engines/wealth.py
"""
MODERN MAGIC FORMULA
Philosophy: Greenblatt (EBIT/EV) + Crypto Staking Yield
Target: High Quality + High Yield
"""

from typing import Any

import pandas as pd


class MagicRanker:
    def __init__(self):
        # SIMULATED LIVE DATA FEED (In production: yFinance + CoinGecko)
        self.market_data = [
            {
                "ticker": "AAPL",
                "type": "STOCK",
                "yield": 0.035,
                "quality": 0.92,
            },  # Buybacks (Simulated Yield)
            {"ticker": "BTC", "type": "CRYPTO", "yield": 0.000, "quality": 0.98},  # Store of Value
            {"ticker": "SOL", "type": "CRYPTO", "yield": 0.072, "quality": 0.85},  # Staking
            {"ticker": "USDC", "type": "STABLE", "yield": 0.051, "quality": 1.00},  # Treasury
        ]

    def rank_assets(self) -> pd.DataFrame:
        """
        Ranks assets based on the weighted sum of their Quality and Yield ranks.
        Lower Rank Sum = Better.
        """
        df = pd.DataFrame(self.market_data)

        # 1. Rank by Yield (Higher is Better)
        df["rank_yield"] = df["yield"].rank(ascending=False)

        # 2. Rank by Quality (Higher is Better)
        df["rank_quality"] = df["quality"].rank(ascending=False)

        # 3. Magic Formula: Sum of Ranks
        df["magic_score"] = df["rank_yield"] + df["rank_quality"]

        # 4. Sort (Lowest Score Wins)
        df_sorted = df.sort_values(by="magic_score", ascending=True)

        return df_sorted

    def get_top_pick(self) -> dict[str, Any]:
        """Returns the Sovereign Asset Choice."""
        df = self.rank_assets()
        top = df.iloc[0]
        return top.to_dict()


# Singleton
reactor = MagicRanker()
