"""
Commerce Mall models.

Handles products, orders, payments, and virtual shopping.
"""

import uuid
from enum import StrEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class PaymentStatus(StrEnum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Product(Base):
    """Product catalog model."""

    __tablename__ = "commerce_products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Product details
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    sku = Column(String(100), unique=True, index=True)

    # Media
    image_urls = Column(JSON)  # List of product images
    model_3d_url = Column(String(1000))  # 3D model for VR
    ar_preview_url = Column(String(1000))

    # ShadowTag verification
    shadowtag_verified = Column(Boolean, default=False, index=True)
    shadowtag_signature = Column(String(500))
    supply_chain_provenance = Column(JSON)  # Verified origin trail

    # Categorization
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    tags = Column(JSON)
    brand = Column(String(200), index=True)

    # Inventory
    stock_quantity = Column(Integer, default=0)
    is_in_stock = Column(Boolean, default=True, index=True)
    restock_date = Column(DateTime(timezone=True))

    # Revenue
    revenue_cents = Column(Integer, default=0)
    units_sold = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price_cents={self.price_cents})>"


class Cart(Base):
    """Shopping cart model."""

    __tablename__ = "commerce_carts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    items = Column(JSON, default=list)  # [{product_id, quantity, price_cents}]
    total_cents = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="carts")

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, total_cents={self.total_cents})>"


class Order(Base):
    """Order model."""

    __tablename__ = "commerce_orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Order details
    total_cents = Column(Integer, nullable=False)
    subtotal_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, default=0)
    shipping_cents = Column(Integer, default=0)

    # Shipping
    shipping_address = Column(JSON)  # Full address object
    shipping_method = Column(String(100))
    tracking_number = Column(String(200))

    # Payment
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    payment_method = Column(String(50))

    # Revenue attribution
    platform_fee_cents = Column(Integer)  # ShadowTag-v4's cut (15%)
    merchant_revenue_cents = Column(Integer)

    # Status
    is_fulfilled = Column(Boolean, default=False, index=True)
    fulfilled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)

    def __repr__(self):
        return (
            f"<Order(id={self.id}, total_cents={self.total_cents}, status={self.payment_status})>"
        )


class OrderItem(Base):
    """Individual items in an order."""

    __tablename__ = "commerce_order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(
        String(36), ForeignKey("commerce_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id = Column(String(36), ForeignKey("commerce_products.id"), nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)  # Price at time of order
    subtotal_cents = Column(Integer, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


class Payment(Base):
    """Payment transaction model."""

    __tablename__ = "commerce_payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(
        String(36),
        ForeignKey("commerce_orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)

    # Payment provider
    provider = Column(String(50))  # stripe, paypal, etc.
    provider_transaction_id = Column(String(200), unique=True, index=True)

    # Metadata
    payment_method_type = Column(String(50))  # card, crypto, etc.
    last_4_digits = Column(String(4))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))

    error_message = Column(Text)

    # Relationships
    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, amount_cents={self.amount_cents}, status={self.status})>"
