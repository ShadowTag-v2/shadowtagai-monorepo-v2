import json
import os
from datetime import datetime


class Ledger:
    """
    The War Chest Ledger.
    Tracks inflows (Revenue) and outflows (Costs).
    """

    def __init__(self, storage_path: str = "/tmp/treasury_ledger.json"):
        self.storage_path = storage_path
        self.balance = 0.0
        self.transactions: list[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    self.balance = data.get("balance", 0.0)
                    self.transactions = data.get("transactions", [])
            except Exception as e:
                print(f"Error loading ledger: {e}")

    def _save(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump({"balance": self.balance, "transactions": self.transactions}, f, indent=2)
        except Exception as e:
            print(f"Error saving ledger: {e}")

    def credit(self, amount: float, source: str, description: str) -> float:
        """Add funds to the War Chest."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")

        self.balance += amount
        self._record("CREDIT", amount, source, description)
        self._save()
        return self.balance

    def debit(self, amount: float, requester: str, reason: str) -> bool:
        """Deduct funds from the War Chest."""
        if amount <= 0:
            raise ValueError("Debit amount must be positive")

        if self.balance >= amount:
            self.balance -= amount
            self._record("DEBIT", amount, requester, reason)
            self._save()
            return True
        return False

    def _record(self, type: str, amount: float, entity: str, description: str):
        self.transactions.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "type": type,
                "amount": amount,
                "entity": entity,
                "description": description,
                "balance_after": self.balance,
            }
        )

    def get_balance(self) -> float:
        return self.balance

    def get_history(self) -> list[dict]:
        return self.transactions
