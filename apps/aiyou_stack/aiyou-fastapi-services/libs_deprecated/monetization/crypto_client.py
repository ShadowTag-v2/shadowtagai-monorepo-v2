import os


class CryptoGate:
    @staticmethod
    def get_deposit_address(currency: str = "BTC") -> str:
        """
        The Bag Man.
        Returns a direct deposit address from Environment.
        """
        # Default to the burn address if not set (Safety)
        wallet = os.getenv(f"CRYPTO_WALLET_{currency}", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

        # Return as URI for QR Codes
        if currency == "BTC":
            return f"bitcoin:{wallet}"
        if currency == "ETH":
            return f"ethereum:{wallet}"

        return wallet
