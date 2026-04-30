from datetime import datetime

from pydantic import BaseModel


class LeakWarning(BaseModel):
    timestamp: datetime
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    estimated_loss: float
    recommendation: str


class RevenueLeakDetector:
    """Analyzes system logs to identify unmonetized value and revenue leaks."""

    def __init__(self, token_cost_per_1k: float = 0.002, min_margin: float = 0.5):
        self.token_cost_per_1k = token_cost_per_1k
        self.min_margin = min_margin

    def analyze_transaction(self, log_entry: dict) -> LeakWarning | None:
        """Analyze a single transaction log for revenue leaks.
        Expected log_entry format:
        {
            "timestamp": "iso-str",
            "tokens_used": int,
            "revenue_generated": float,
            "tier": "free" | "pro" | "enterprise"
        }
        """
        tokens = log_entry.get("tokens_used", 0)
        revenue = log_entry.get("revenue_generated", 0.0)
        tier = log_entry.get("tier", "unknown")

        cost = (tokens / 1000) * self.token_cost_per_1k
        margin = (revenue - cost) / revenue if revenue > 0 else -1.0

        # Check 1: High consumption on Free Tier
        if tier == "free" and tokens > 10000:
            return LeakWarning(
                timestamp=datetime.now(),
                severity="HIGH",
                description=f"Free tier user consumed {tokens} tokens costing ${cost:.4f}",
                estimated_loss=cost,
                recommendation="Throttle user or prompt upgrade to Pro.",
            )

        # Check 2: Negative Margin on Paid Tiers
        if revenue > 0 and margin < self.min_margin:
            return LeakWarning(
                timestamp=datetime.now(),
                severity="MEDIUM",
                description=f"Transaction margin {margin:.2%} is below target {self.min_margin:.0%}",
                estimated_loss=(revenue * self.min_margin) - (revenue - cost),  # Gap to target
                recommendation="Optimize prompt tokens or increase pricing.",
            )

        return None
