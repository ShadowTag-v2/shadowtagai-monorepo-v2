"""The Gemini Store (Digital Mall) - Marketplace Core
Governed AI marketplace with pre-execution compliance verification.
Ported from Legacy Archives (AiU Digital Mall).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Integration with Antigravity Governance
# In a full implementation, we would import JudgeSix here,
# but we will likely orchestrate that via the StoreManager Agent.


class VendorStatus(Enum):
    """Vendor verification status"""

    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class ProductStatus(Enum):
    """Product listing status"""

    PENDING = "pending"  # Awaiting Compliance validation
    ACTIVE = "active"  # Approved and listed
    SUSPENDED = "suspended"  # Temporarily unavailable
    REJECTED = "rejected"  # Failed compliance


@dataclass
class Vendor:
    """Verified AI service vendor"""

    vendor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    status: VendorStatus = VendorStatus.PENDING
    compliance_verified: bool = False
    compliance_score: float = 0.0  # 0.0-1.0
    products: list[str] = field(default_factory=list)  # Product IDs
    revenue_share: float = 0.88  # Vendor keeps 88%, Mall takes 12%
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Product:
    """AI product/service listing"""

    product_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""  # e.g., "ai_model", "dataset", "api_service", "agent"
    price: float = 0.0  # USD
    pricing_model: str = "one_time"  # one_time, subscription, per_use
    status: ProductStatus = ProductStatus.PENDING
    compliance_validated: bool = False
    compliance_frameworks: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Transaction:
    """Marketplace transaction"""

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str = ""
    vendor_id: str = ""
    buyer_id: str = ""
    amount: float = 0.0
    mall_fee: float = 0.0  # 12% of amount
    vendor_payout: float = 0.0  # 88% of amount
    status: str = "pending"  # pending, completed, failed, refunded
    compliance_check_passed: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())


class GeminiStore:
    """The Gemini Store - Governed AI Marketplace

    Features:
    - Pre-execution compliance for all listings (JudgeSix validation)
    - 12% transaction fee (vs. 30% standard)
    - Verified vendor badges
    """

    def __init__(self, fee_percentage: float = 0.12):
        """Initialize Gemini Store

        Args:
            fee_percentage: Marketplace fee (default 12%)

        """
        self.fee_percentage = fee_percentage
        self.vendors: dict[str, Vendor] = {}
        self.products: dict[str, Product] = {}
        self.transactions: dict[str, Transaction] = {}

        # Statistics
        self.stats = {
            "total_vendors": 0,
            "verified_vendors": 0,
            "total_products": 0,
            "active_products": 0,
            "total_gmv": 0.0,
            "total_fees_collected": 0.0,
        }

    def register_vendor(self, name: str, email: str) -> Vendor:
        """Register a new vendor (initially PENDING).
        """
        vendor = Vendor(name=name, email=email)
        self.vendors[vendor.vendor_id] = vendor
        self.stats["total_vendors"] += 1
        return vendor

    def approve_vendor(self, vendor_id: str, compliance_score: float = 1.0) -> bool:
        """Approve a vendor after verification.
        """
        vendor = self.vendors.get(vendor_id)
        if not vendor:
            return False

        vendor.status = VendorStatus.VERIFIED
        vendor.compliance_verified = True
        vendor.compliance_score = compliance_score
        self.stats["verified_vendors"] += 1
        return True

    def list_product(
        self, vendor_id: str, name: str, description: str, price: float, category: str = "agent",
    ) -> Product:
        """Submit a product for listing (starts as PENDING).
        """
        # Verify vendor exists and is verified
        vendor = self.vendors.get(vendor_id)
        if not vendor or vendor.status != VendorStatus.VERIFIED:
            raise ValueError(f"Vendor {vendor_id} not verified")

        product = Product(
            vendor_id=vendor_id, name=name, description=description, price=price, category=category,
        )

        self.products[product.product_id] = product
        vendor.products.append(product.product_id)
        self.stats["total_products"] += 1

        return product

    def approve_product(self, product_id: str, risk_score: float = 0.0) -> bool:
        """Approve a product after JudgeSix validation.
        """
        product = self.products.get(product_id)
        if not product:
            return False

        product.status = ProductStatus.ACTIVE
        product.compliance_validated = True
        product.risk_score = risk_score
        self.stats["active_products"] += 1
        return True

    def purchase(self, product_id: str, buyer_id: str) -> Transaction:
        """Process purchase transaction
        """
        product = self.products.get(product_id)
        if not product or product.status != ProductStatus.ACTIVE:
            raise ValueError(f"Product {product_id} not available")

        vendor = self.vendors.get(product.vendor_id)
        if not vendor or vendor.status != VendorStatus.VERIFIED:
            raise ValueError(f"Vendor {product.vendor_id} not verified")

        # Calculate fees
        amount = product.price
        mall_fee = amount * self.fee_percentage
        vendor_payout = amount - mall_fee

        # Create transaction
        transaction = Transaction(
            product_id=product_id,
            vendor_id=product.vendor_id,
            buyer_id=buyer_id,
            amount=amount,
            mall_fee=mall_fee,
            vendor_payout=vendor_payout,
            status="completed",
            compliance_check_passed=True,
        )

        self.transactions[transaction.transaction_id] = transaction

        # Update statistics
        self.stats["total_gmv"] += amount
        self.stats["total_fees_collected"] += mall_fee

        return transaction

    def get_catalog(self) -> list[Product]:
        """Return all active products"""
        return [p for p in self.products.values() if p.status == ProductStatus.ACTIVE]
