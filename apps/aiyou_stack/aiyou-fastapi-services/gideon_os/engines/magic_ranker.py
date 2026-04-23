# /home/jupyter/gideon_os/engines/magic_ranker.py
import pandas as pd
import yfinance as yf
from pycoingecko import CoinGeckoAPI
from scipy.stats import rankdata


class ModernMagicFormula:
    def __init__(self):
        self.cg = CoinGeckoAPI()

    def get_stock_metrics(self, tickers):
        """Classic Greenblatt: EBIT/EV + ROC"""
        data = []
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                info = stock.info
                # Calculate Greenblatt Metrics
                ebit = info.get("ebitda", 0)  # Proxy if EBIT missing
                ev = info.get("enterpriseValue", 1)
                earnings_yield = ebit / ev if ev else 0

                # ROC = EBIT / (NetFixed + WorkingCapital)
                # Simplified for API availability: Return on Assets
                roc = info.get("returnOnAssets", 0)

                data.append({"ticker": t, "ey": earnings_yield, "roc": roc, "type": "STOCK"})
            except Exception:
                continue
        return pd.DataFrame(data)

    def get_crypto_metrics(self, coins=None):
        """Modern Crypto: Staking Yield + Inverse NVT"""
        if coins is None:
            coins = ["bitcoin", "ethereum", "solana", "cardano"]
        data = []
        market_data = self.cg.get_coins_markets(vs_currency="usd", ids=",".join(coins))

        # Hardcoded yields for MVP (Replace with StakingRewards API for production)
        yields = {"bitcoin": 0.0, "ethereum": 0.035, "solana": 0.07, "cardano": 0.03}

        for coin in market_data:
            c_id = coin["id"]
            # NVT Proxy: Market Cap / Total Volume (Lower is better/cheaper)
            nvt = coin["market_cap"] / coin["total_volume"] if coin["total_volume"] else 999

            # "Earnings Yield" = Staking Yield
            ey = yields.get(c_id, 0)

            # "Quality" = Inverse NVT (High volume relative to cap)
            quality = 1 / nvt

            data.append({"ticker": c_id.upper(), "ey": ey, "roc": quality, "type": "CRYPTO"})
        return pd.DataFrame(data)

    def generate_rankings(self):
        # 1. Fetch Data
        print("...Fetching Market Data...")
        stocks = self.get_stock_metrics(["AAPL", "MSFT", "GOOGL", "META", "TSLA", "AMZN"])
        cryptos = self.get_crypto_metrics()

        # 2. Merge & Rank
        df = pd.concat([stocks, cryptos])

        # 3. Magic Formula Ranking (Higher is better)
        df["rank_ey"] = rankdata(df["ey"])
        df["rank_roc"] = rankdata(df["roc"])
        df["magic_score"] = df["rank_ey"] + df["rank_roc"]

        return df.sort_values("magic_score", ascending=False)
