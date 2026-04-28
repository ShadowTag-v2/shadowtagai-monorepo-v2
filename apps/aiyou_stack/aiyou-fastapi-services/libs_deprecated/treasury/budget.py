# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .ledger import Ledger


class BudgetEnforcer:
    """Enforces spending rules based on the Ledger."""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        # Spending limits per category (Mock rules for now)
        self.limits = {
            "compute": 100.0,  # Max $100 compute per transaction
            "api_call": 1.0,  # Max $1 per API call
        }

    def can_spend(self, amount: float, category: str) -> bool:
        """Check if a spend is within limits and funds are available."""
        if category in self.limits and amount > self.limits[category]:
            return False

        # Check actual balance
        return self.ledger.get_balance() >= amount

    def approve_transaction(
        self,
        amount: float,
        requester: str,
        category: str,
        reason: str,
    ) -> bool:
        """Attempt to authorize and execute a debit."""
        if self.can_spend(amount, category):
            return self.ledger.debit(amount, requester, f"[{category}] {reason}")
        return False
