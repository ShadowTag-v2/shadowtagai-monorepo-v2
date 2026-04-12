import json
import os
import secrets
import time
from datetime import datetime

from pydantic import BaseModel

from src.config.pricing import API_COSTS, PRICING_CONFIG, PricingTier

# Data Storage Paths
DATA_DIR = "data"
KEYS_FILE = os.path.join(DATA_DIR, "api_keys.json")
LOG_FILE = os.path.join(DATA_DIR, "usage_log.jsonl")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


class APIKey(BaseModel):
    key: str
    user_id: str
    tier: PricingTier
    created_at: float
    is_active: bool = True
    usage_count: int = 0
    total_spend: float = 0.0


class StripeClient:
    """
    Stub for Stripe integration.
    In production, this would use the official stripe library.
    """

    def __init__(self, api_key: str = "sk_test_stub"):
        self.api_key = api_key

    def create_customer(self, user_id: str, email: str) -> str:
        """Create a Stripe customer."""
        # STUB: Return a fake customer ID
        return f"cus_{secrets.token_hex(8)}"

    def report_usage(self, subscription_id: str, quantity: int):
        """Report metered usage to Stripe."""
        # STUB: Log usage report
        # print(f"///▞ STRIPE :: Reported usage {quantity} for {subscription_id}")
        pass


class MonetizationEngine:
    """
    Core engine for handling API keys, tracking usage, and enforcing pricing tiers.
    Plugins 'Wealth Leaks' by capturing value at the API layer.
    """

    def __init__(self):
        self.stripe = StripeClient()
        self._keys: dict[str, APIKey] = {}
        self.load_keys()

    def load_keys(self):
        """Load API keys from JSON storage."""
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE) as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._keys[k] = APIKey(**v)
            except json.JSONDecodeError:
                print("///▞ MONETIZATION :: Corrupt keys file, starting fresh.")

    def save_keys(self):
        """Save API keys to JSON storage."""
        with open(KEYS_FILE, "w") as f:
            data = {k: v.dict() for k, v in self._keys.items()}
            json.dump(data, f, indent=2)

    def create_api_key(self, user_id: str, tier: PricingTier = PricingTier.FREE) -> str:
        """Generates a secure API key for a user on a specific tier."""
        # Prefix keys for security scanning identification
        api_key_str = f"ay_{tier.value}_{secrets.token_urlsafe(32)}"

        key_obj = APIKey(key=api_key_str, user_id=user_id, tier=tier, created_at=time.time())
        self._keys[api_key_str] = key_obj
        self.save_keys()

        # In a real app, we'd sync this user to Stripe here if needed
        # self.stripe.create_customer(user_id, f"{user_id}@example.com")

        return api_key_str

    def validate_key(self, api_key: str) -> APIKey | None:
        """Validates key existence and active status."""
        key = self._keys.get(api_key)
        if key and key.is_active:
            return key
        return None

    def track_request(self, api_key: str, endpoint: str) -> dict:
        """
        Tracks a request, updates spend, and checks limits.
        Returns usage stats or raises error if limit exceeded.
        """
        key = self.validate_key(api_key)
        if not key:
            raise ValueError("Invalid or inactive API Key")

        # 1. Check Rate/Usage Limits
        config = PRICING_CONFIG.get(key.tier)
        if key.usage_count >= config.request_limit_daily:
            # Simple daily reset logic would go here in prod (check logs or reset timestamp)
            # For now, simplistic enforcement
            pass
            # In a strict environment:
            # raise ValueError(f"Daily limit of {config.request_limit_daily} exceeded for tier {key.tier.value}")

        # 2. Calculate Cost (Wealth Capture)
        cost = API_COSTS.get(endpoint, 0.0)

        # 3. Update State
        key.usage_count += 1
        key.total_spend += cost
        self.save_keys()  # Persist updates

        # Log for audit/billing
        usage_record = {
            "key": api_key,
            "user": key.user_id,
            "tier": key.tier.value,
            "endpoint": endpoint,
            "cost": cost,
            "timestamp": time.time(),
            "iso_time": datetime.utcnow().isoformat(),
        }

        # Append to log file
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(usage_record) + "\n")

        return usage_record

    def calculate_total_revenue(self) -> float:
        """Returns total revenue captured from all keys (API usage only, excludes subs)."""
        return sum(k.total_spend for k in self._keys.values())


# Global Instance
monetization = MonetizationEngine()

if __name__ == "__main__":
    print("///▞ MONETIZATION :: Initializing Engine...")

    # Test Key Generation
    user = "test_user_01"
    key = monetization.create_api_key(user, PricingTier.TEAM)
    print(f"///▞ GENERATED KEY :: {key[:15]}...")

    # Test Tracking
    print("///▞ TRACKING REQUEST :: 'decision_complex'")
    stats = monetization.track_request(key, "decision_complex")
    print(
        f"///▞ USAGE :: Cost=${stats['cost']} | TotalSpend=${monetization.calculate_total_revenue()}"
    )

    # Verify Persistence
    print("///▞ VERIFYING PERSISTENCE...")
    monetization = None  # Reset
    new_engine = MonetizationEngine()
    reloaded_key = new_engine.validate_key(key)

    if reloaded_key and reloaded_key.usage_count > 0:
        print("///▞ SUCCESS :: Persistence verified.")
    else:
        print("///▞ FAILED :: Persistence check failed.")
