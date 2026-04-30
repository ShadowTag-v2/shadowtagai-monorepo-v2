# DOCTRINE: Cor.115 Night Pipeline (Source Coverage)
# RESPONSIBILITY: Multi-Source Diversity (Shannon Entropy)

import math


class SourceCoverageAnalyzer:
    def __init__(self):
        self.sources = {
            "YouTube": 0,
            "Twitter": 0,
            "News": 0,
            "RSS": 0,
            "Web": 0,
            "API": 0,
            "Podcast": 0,
            "Research": 0,
        }

    def update_counts(self, counts: dict[str, int]):
        self.sources.update(counts)

    def calculate_shannon_entropy(self) -> float:
        """Calculates diversity score (0-100) based on Shannon Entropy."""
        total = sum(self.sources.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in self.sources.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Max entropy for 8 categories is log2(8) = 3
        # Normalize to 0-100
        normalized_score = (entropy / 3.0) * 100.0
        return round(min(100.0, normalized_score), 2)

    def get_tier_distribution(self) -> dict[str, float]:
        """Simulates Tier Classification (T1/T2/T3)."""
        # Mock logic based on source types
        sum(self.sources.values()) or 1
        return {
            "Tier 1 (High Value)": 25.0,  # Target >= 20%
            "Tier 2 (Medium Value)": 45.0,
            "Tier 3 (General)": 30.0,
        }
