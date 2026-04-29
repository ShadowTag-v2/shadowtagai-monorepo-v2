# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from typing import Any

from src.economy.mall import GeminiStore, Transaction, Vendor
from src.governance.Claude_Code_6.core import JudgeSixEngine


class StoreManager:
    """The Shopkeeper.
    Manages the Gemini Store, onboardings, and compliance vetting.
    """

    def __init__(self, judge: JudgeSixEngine):
        self.store = GeminiStore()
        self.judge = judge

    def onboard_vendor(self, name: str, email: str) -> Vendor:
        """Register and auto-approve a vendor (MVP)."""
        vendor = self.store.register_vendor(name, email)
        # MVP: Auto-verify
        # In production, we would run ID checks here.
        self.store.approve_vendor(vendor.vendor_id)
        return vendor

    def list_product(
        self,
        vendor_id: str,
        name: str,
        description: str,
        price: float,
        category: str,
        content_to_scan: str = None,
    ) -> dict[str, Any]:
        """Submit a product, vet it with JudgeSix, and list it if approved."""
        # 1. Draft Listing
        try:
            product = self.store.list_product(vendor_id, name, description, price, category)
        except ValueError as e:
            return {"status": "ERROR", "reason": str(e)}

        # 2. JudgeSix Vetting (Compliance as a Service)
        scan_payload = {"content": content_to_scan or description, "type": "PRODUCT_LISTING"}

        # We assume a standard mission for vetting
        decision = self.judge.execute_mission(
            mission_id=f"VET-{product.product_id[:8]}",
            telemetry={},
            mission_type="ROUTINE",
            payload=scan_payload,
        )

        if decision.approved:
            self.store.approve_product(
                product.product_id,
                risk_score=0.1,
            )  # Mock low risk if approved
            return {
                "status": "LISTED",
                "product_id": product.product_id,
                "risk_report": decision.explanation or "Clean",
            }
        return {
            "status": "REJECTED",
            "product_id": product.product_id,
            "reason": decision.explanation,
            "mitigation": decision.mitigation_choices,
        }

    def purchase_product(self, product_id: str, buyer_id: str) -> Transaction:
        """Execute a purchase."""
        return self.store.purchase(product_id, buyer_id)

    def get_catalog(self) -> list[dict]:
        """Get public catalog."""
        return [
            {
                "id": p.product_id,
                "name": p.name,
                "price": p.price,
                "vendor": self.store.vendors[p.vendor_id].name,
                "category": p.category,
            }
            for p in self.store.get_catalog()
        ]

    def get_transactions(self) -> list[Transaction]:
        """Get all transactions for the ledger."""
        return list(self.store.transactions.values())
