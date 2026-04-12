class TrustRouter:
    def __init__(self):
        # Rule Set: Jurisdiction -> {Features}
        self.jurisdictions = {
            "DE_STATUTORY": {
                "type": "Statutory Trust",
                "cgt": 0.0,
                "privacy": "High",
                "crypto_friendly": True,
            },
            "SG_GPL": {
                "type": "Global Investor",
                "cgt": 0.0,
                "privacy": "Med",
                "crypto_friendly": True,
            },
            "WY_DAO": {
                "type": "DAO LLC",
                "cgt": "Pass-thru",
                "privacy": "High",
                "crypto_friendly": True,
            },
            "UK_LTD": {"type": "Limited", "cgt": 0.20, "privacy": "Low", "crypto_friendly": False},
        }

    def route(self, profile):
        """Selects best structure based on asset mix and tax residency."""
        score = {}
        for code, rules in self.jurisdictions.items():
            s = 0
            # 1. Crypto Check
            if profile["has_crypto"] and rules["crypto_friendly"]:
                s += 5
            elif profile["has_crypto"] and not rules["crypto_friendly"]:
                s -= 10

            # 2. Tax Optimization
            if profile["seek_tax_efficiency"] and rules["cgt"] == 0.0:
                s += 5

            # 3. Privacy
            if profile["seek_privacy"] and rules["privacy"] == "High":
                s += 3

            score[code] = s

        best = max(score, key=score.get)
        return self.jurisdictions[best], best
